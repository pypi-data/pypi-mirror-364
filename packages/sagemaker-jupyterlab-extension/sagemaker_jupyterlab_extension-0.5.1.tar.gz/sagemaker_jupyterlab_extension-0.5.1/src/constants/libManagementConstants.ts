export const PACKAGE_INSTALLER_COMMANDS = {
  restartServer: 'restart-jupyter-server\n',
  micromambaInstall: 'micromamba install --freeze-installed -y',
} as const;

export const PACKAGE_INSTALLER_LABELS = {
  restartServer: 'Restart Server',
  viewTerminal: 'View in terminal',
} as const;

export enum LIB_MANAGEMENT_COMMAND_IDS {
  EDIT_LIBRARY_CONFIG = 'edit-library-config',
}

export enum CONNECTION_TYPE {
  IAM = 'iam',
}

export const LIB_MANAGEMENT_CONFIG = {
  fileType: {
    name: 'libs-config',
    pattern: '.libs.json',
    mimeTypes: ['application/json'],
  },
  factory: {
    name: 'library-config-editor',
  },
  launcher: {
    category: 'Other',
    rank: 1,
  },
} as const;

export const initConfig = {
  ApplyChangeToSpace: false,
  Python: {
    CondaPackages: {
      Channels: [],
      PackageSpecs: [],
    },
  },
};

export enum COMMAND_STATUS {
  RUNNING,
  SUCCESS,
  FAILURE,
}

export const COMMAND_MONITOR = {
  printExitCodeCommand: 'echo "EXIT_CODE: $?"',
  printExitCode: 'EXIT_CODE:',
  printExitCodeZero: 'EXIT_CODE: 0',
  packagesAlreadyInstalled: 'All requested packages already installed',
  pollInterval: 1000,
} as const;

export const VALID_NAME_PATTERN = '^[a-zA-Z0-9._:/=<>!~^*,|-]+$';
// eslint-disable-next-line no-control-regex
export const TERMINAL_OUTPUT_CLEAN_PATTERN = /\x1B\[[?0-9;]*[a-zA-Z]|\r/g;

export const LIB_MANAGEMENT_DEFAULTS = {
  selectedType: 'Python',
  selectedSource: 'CondaPackages',
} as const;
