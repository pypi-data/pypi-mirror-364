import { Notification } from '@jupyterlab/apputils';
import { Terminal } from '@jupyterlab/services';
import { Terminal as TerminalWidget } from '@jupyterlab/terminal';
import { ReadonlyJSONObject } from '@lumino/coreutils';
import { ILogger } from '@amzn/sagemaker-jupyterlab-extension-common';
import { recordMetric } from './metrics';
import { createCommandPromise } from './CommandMonitor';
import { PACKAGE_INSTALLER_COMMANDS, PACKAGE_INSTALLER_LABELS, il18Strings } from '../../constants';

interface InstallationResult {
  alreadyInstalled: boolean;
  output: string;
}

interface PackageConfig {
  packages: string[];
  channels: string[];
}

interface TerminalState {
  terminal: Terminal.ITerminalConnection;
  widget: TerminalWidget;
  opened: boolean;
  warningNotificationId?: string;
}

type CreateTerminalFn = () => Promise<Terminal.ITerminalConnection>;
type OpenTerminalFn = (widget: TerminalWidget) => void;

class PackageInstaller {
  private readonly createTerminal: CreateTerminalFn;
  private readonly openTerminal: OpenTerminalFn;
  private readonly logger?: ILogger;
  private readonly startTime: number;

  constructor(createTerminal: CreateTerminalFn, openTerminal: OpenTerminalFn, logger?: ILogger) {
    this.createTerminal = createTerminal;
    this.openTerminal = openTerminal;
    this.logger = logger;
    this.startTime = Date.now();
  }

  private extractPackageConfig(configData: ReadonlyJSONObject): PackageConfig | null {
    const pythonConfig = configData.Python as ReadonlyJSONObject | undefined;
    if (!pythonConfig?.CondaPackages) return null;

    const condaConfig = pythonConfig.CondaPackages as ReadonlyJSONObject;
    const packages = (condaConfig.PackageSpecs as string[]) || [];
    const channels = (condaConfig.Channels as string[]) || [];

    return packages.length > 0 ? { packages, channels } : null;
  }

  private buildInstallCommand({ packages, channels }: PackageConfig): string {
    const channelArgs = channels.map((channel) => `-c "${channel}"`).join(' ');
    const packageArgs = packages.map((pkg) => `"${pkg}"`).join(' ');
    return `${PACKAGE_INSTALLER_COMMANDS.micromambaInstall} ${channelArgs} ${packageArgs}`;
  }

  private createTerminalWidget(terminal: Terminal.ITerminalConnection, prefix: string): TerminalWidget {
    const widget = new TerminalWidget(terminal);
    widget.id = `${prefix}${Date.now()}`;
    widget.title.closable = true;
    return widget;
  }

  private async restartServer(): Promise<void> {
    const terminal = await this.createTerminal();
    const widget = this.createTerminalWidget(terminal, 'restartServer');
    this.openTerminal(widget);
    terminal.send({ type: 'stdin', content: [PACKAGE_INSTALLER_COMMANDS.restartServer] });
  }

  private recordInstallationMetric(success: boolean, output: string): void {
    const latency = Date.now() - this.startTime;
    recordMetric('Package Installation', {
      latency,
      success: success ? 1 : 0,
      error: success ? 0 : 1,
      output,
    });
  }

  private handleTerminalView(terminalState: TerminalState, showWarning = true): void {
    if (terminalState.terminal.isDisposed) {
      Notification.error(il18Strings.LibManagement.terminalDisposed);
      return;
    }

    terminalState.opened = true;
    this.openTerminal(terminalState.widget);

    if (showWarning) {
      terminalState.warningNotificationId = Notification.warning(il18Strings.LibManagement.terminalWarning, {
        autoClose: false,
        actions: [],
      });
    }
  }

  private getSuccessMessage(result: InstallationResult): string {
    return result.alreadyInstalled ? il18Strings.LibManagement.allInstalled : il18Strings.LibManagement.installSuccess;
  }

  private createRestartAction() {
    return {
      label: PACKAGE_INSTALLER_LABELS.restartServer,
      callback: () => this.restartServer(),
    };
  }

  private createViewTerminalAction(terminalState: TerminalState, showWarning = true) {
    return {
      label: PACKAGE_INSTALLER_LABELS.viewTerminal,
      callback: () => this.handleTerminalView(terminalState, showWarning),
    };
  }

  private handleInstallationSuccess(result: InstallationResult, terminalState: TerminalState): void {
    if (terminalState.opened) {
      const message = this.getSuccessMessage(result);
      const actions = result.alreadyInstalled ? [] : [this.createRestartAction()];
      Notification.success(message, { actions, autoClose: false });
    } else {
      // For terminal not opened, show notification with restart button only if not already installed
      const actions = result.alreadyInstalled ? [] : [this.createRestartAction()];
      Notification.success(this.getSuccessMessage(result), { actions, autoClose: false });
    }
  }

  private handleInstallationError(error: Error, terminalState: TerminalState): void {
    this.recordInstallationMetric(false, error.message);

    if (terminalState.opened) {
      Notification.error(il18Strings.LibManagement.installFailed, {
        autoClose: false,
        actions: [],
      });
    }
  }

  private setupNotificationHandlers(installPromise: Promise<InstallationResult>, terminalState: TerminalState): void {
    Notification.promise(installPromise as Promise<any>, {
      pending: {
        message: il18Strings.LibManagement.installing,
        options: {
          actions: [this.createViewTerminalAction(terminalState)],
          autoClose: false,
        },
      },
      success: {
        message: (result: unknown) => {
          const installResult = result as InstallationResult;
          this.recordInstallationMetric(true, installResult.output);
          if (terminalState.warningNotificationId) {
            Notification.dismiss(terminalState.warningNotificationId);
          }
          return this.getSuccessMessage(installResult);
        },
        options: {
          actions: [],
          autoClose: 1,
        },
      },
      error: {
        message: (reason: unknown) => {
          const errorMessage = reason instanceof Error ? reason.message : String(reason);
          this.recordInstallationMetric(false, errorMessage);
          if (terminalState.warningNotificationId) {
            Notification.dismiss(terminalState.warningNotificationId);
          }
          return il18Strings.LibManagement.installFailed;
        },
        options: {
          actions: [this.createViewTerminalAction(terminalState, false)],
          autoClose: false,
        },
      },
    });

    installPromise
      .then((result) => this.handleInstallationSuccess(result, terminalState))
      .catch((error) => this.handleInstallationError(error, terminalState))
      .finally(() => {
        if (terminalState.warningNotificationId) {
          Notification.dismiss(terminalState.warningNotificationId);
        }
      });
  }

  async install(configData: ReadonlyJSONObject): Promise<InstallationResult | void> {
    if (!configData.Python) return;

    const packageConfig = this.extractPackageConfig(configData);
    if (!packageConfig) return;

    this.logger?.info({ Message: 'Installing packages and extensions from config' });

    const terminal = await this.createTerminal();
    const terminalState: TerminalState = {
      terminal,
      widget: this.createTerminalWidget(terminal, 'installLab'),
      opened: false,
    };

    const command = this.buildInstallCommand(packageConfig);
    const installPromise = createCommandPromise(terminal, [command], this.logger);

    this.setupNotificationHandlers(installPromise, terminalState);

    return installPromise;
  }
}

/**
 * Installs packages from configuration data
 *
 * @param configData - The configuration data containing package information
 * @param createTerminal - Function to create a terminal
 * @param openTerminal - Function to open a terminal widget
 * @param logger - Optional logger for recording events
 * @returns Promise that resolves when installation is complete
 */
export async function installPackagesFromConfig(
  configData: ReadonlyJSONObject,
  createTerminal: CreateTerminalFn,
  openTerminal: OpenTerminalFn,
  logger?: ILogger,
): Promise<InstallationResult | void> {
  const installer = new PackageInstaller(createTerminal, openTerminal, logger);
  return installer.install(configData);
}
