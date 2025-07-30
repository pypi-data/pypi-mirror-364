import { Terminal } from '@jupyterlab/services';
import { ILogger } from '@amzn/sagemaker-jupyterlab-extension-common';
import { COMMAND_STATUS, COMMAND_MONITOR, TERMINAL_OUTPUT_CLEAN_PATTERN, il18Strings } from '../../constants';

/**
 * Creates a promise that resolves when commands complete successfully
 * Monitors terminal output to detect command completion and status
 */
export function createCommandPromise(
  terminal: Terminal.ITerminalConnection,
  commands: string[],
  logger?: ILogger,
): Promise<{ alreadyInstalled: boolean; output: string }> {
  let status = COMMAND_STATUS.RUNNING;
  let executingCommands = commands.length;
  let alreadyInstalled = false;
  let intervalId: number;
  let accumulatedOutput = '';

  // Monitors terminal output for command completion and exit codes
  function terminalMonitor(terminal: Terminal.ITerminalConnection, message: Terminal.IMessage) {
    if (message.type === 'stdout' && message.content) {
      message.content.forEach((content) => {
        if (status === COMMAND_STATUS.RUNNING && typeof content === 'string') {
          // Save stdout for logs
          const cleanContent = content.replace(TERMINAL_OUTPUT_CLEAN_PATTERN, '').trim();
          if (cleanContent) {
            accumulatedOutput += cleanContent + '\n';
          }

          // Check for result of command
          if (content.includes(COMMAND_MONITOR.packagesAlreadyInstalled)) {
            alreadyInstalled = true;
          }
          if (
            !content.includes(COMMAND_MONITOR.printExitCodeCommand) &&
            content.includes(COMMAND_MONITOR.printExitCode)
          ) {
            if (content.includes(COMMAND_MONITOR.printExitCodeZero)) {
              executingCommands--;
              if (!executingCommands) {
                status = COMMAND_STATUS.SUCCESS;
                logger?.info({ Message: il18Strings.LibManagement.successfullyInstalledPackages });
              }
            } else {
              // If any command returns non 0 exit code, stop monitoring and set the status to FAILED
              status = COMMAND_STATUS.FAILURE;
              terminal.messageReceived.disconnect(terminalMonitor);
              logger?.error({ Message: il18Strings.LibManagement.failedToInstallPackages });
            }
          }
        } else if (status === COMMAND_STATUS.RUNNING) {
          // memory leak prevention
          status = COMMAND_STATUS.FAILURE;
          terminal.messageReceived.disconnect(terminalMonitor);
        }
      });
    }
  }
  terminal.messageReceived.connect(terminalMonitor);

  // Join commands with exit code checks
  let command = commands.join(`;${COMMAND_MONITOR.printExitCodeCommand};`);

  command += `;${COMMAND_MONITOR.printExitCodeCommand}\n;`;
  terminal.send({ type: 'stdin', content: [command] });

  // Return promise that resolves when commands complete
  return new Promise<{ alreadyInstalled: boolean; output: string }>((resolve, reject) => {
    intervalId = window.setInterval(() => {
      if (status === COMMAND_STATUS.SUCCESS) {
        clearInterval(intervalId);
        terminal.messageReceived.disconnect(terminalMonitor);
        try {
          terminal.shutdown().catch(() => {
            /* ignore shutdown errors */
          });
        } catch {
          // ignore any shutdown errors
        }
        resolve({ alreadyInstalled, output: accumulatedOutput });
      } else if (status === COMMAND_STATUS.FAILURE) {
        clearInterval(intervalId);
        terminal.messageReceived.disconnect(terminalMonitor);
        reject(new Error(accumulatedOutput));
      }
    }, COMMAND_MONITOR.pollInterval);
  });
}
