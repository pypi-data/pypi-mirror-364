export const il18Strings = {
  SignInSession: {
    closeButton: 'Close',
    signInButton: 'Sign In',
    saveButton: 'Save',
    saveAndRenewButton: 'Save and renew session',
    signinDialog: {
      title: 'Please sign in again',
      restartSessionBody:
        'You were logged out of your account. You are not able to perform actions in your workplace at this time. Please start a new session.',
      loggedOutBody: "You were logged out of your account. Choose 'Sign In' to continue using this workplace.",
    },
    sessionExpiredDialog: {
      title: 'Session Expired please signin',
    },
    renewSessionDialog: {
      title: 'Session expiring soon',
      defaultBodyText: 'If your session expires, you could lose unsaved changes.',
      renewSessionBody:
        'To renew the session, log out from Studio App via "File" -> "Log Out" and then "Sign out" from AWS IAM Identity Center (successor to AWS SSO) user portal.',
      saveAllChanges: 'Do you want to save all changes now?',
      renewSessionNow: 'Do you want to renew your session now?',
      remindText: 'Remind me in 5 minutes',
      soonExpiringSessionBody: 'This session will expire soon.',
      contDownTimerMessage: 'This session will expire ',
      fromNow: 'from now.',
      loseUnsavedChanges: 'If your session expires, you could lose unsaved changes.',
    },
  },
  ResourceUsage: {
    cpuMetricTitle: 'CPU:',
    memoryMetricTitle: 'MEM:',
    storageMetricTitle: 'Storage:',
    instanceMemoryProgressBarTitle: 'Instance MEM',
    instanceMetricsTitle: 'Instance',
    stoargeSpaceLimitDialog: {
      title: 'Free up storage space',
    },
  },
  GitClone: {
    dialogTitle: 'Clone Git Repository',
    repoTitle: 'Git repositories URL(.git):',
    pathTitle: 'Project directory to clone into:',
    afterCloningTitle: 'After cloning',
    openReadMeFilesLabel: 'Open README files.',
    cancelButton: 'Cancel',
    cloneButton: 'Clone',
    errors: {
      directoryNotExistTitle: 'Destination directory doesn’t exist.',
      directoryNotExistBody:
        'The destination directory doesn’t exist. Create this directory and then try cloning the repository again. directory: ',
      localGitCloneExistTitle: 'Repository clone already exists in project.',
      localGitCloneExistBody:
        'It looks like the Git repository has already been cloned into the given directory. Click Dismiss to navigate to your existing clone. repositoy: ',
      noURLErrorTitle: 'Missing valid URL.',
      noURLErrorBody: 'No URL listed to clone the repository. Please input a valid URL ending with ".git".',
      generalCloneErrorTitle: 'Unable to clone repository to project.',
      generalCloneErrorBody:
        'Something went wrong when trying to clone the repository to your project. Please try again later. ',
      failedOptions: 'Failed to handle additional options.',
      failedOptionsBody: 'Something went wrong when trying to open README file within the repo.',
      invalidCloneUrlTitle: 'Invalid URL provided',
      invalidCloneUrlBody: 'The URL provided is not valid. Please input a valid URL to clone.',
    },
  },
  Space: {
    privateSpaceHeader: 'Personal Studio',
    unknownUser: 'Unknown User',
    unknownSpace: 'Unknown Space',
  },
  ProjectsCloneRepo: {
    errorDialog: {
      errorTitle: 'Unable to clone repository',
      defaultErrorMessage: 'Something went wrong when cloning the repository.',
      invalidRequestErrorMessage: 'A request to clone the reposioty is invalid.',
      invalidProjectName: 'Invalid project name: Project does not exist.',
      invalidCloneUrlBody: 'The URL provided is not valid. Please input a valid URL to clone.',
    },
  },
  LibManagement: {
    // Package Installer strings
    installing: 'Installing packages and extensions from saved configuration...',
    allInstalled: 'All packages and extensions already installed',
    installSuccess:
      'Installation completed. Restart the kernel for updated libraries. Restart the server for updated extensions.',
    installFailed: 'Failed to install packages/extensions. Check error logs in terminal.',
    terminalDisposed: 'Terminal is disposed',
    terminalWarning:
      'Closing the terminal will terminate the installation process. This terminal will automatically close once installation complete.',
    // Plugin strings
    environmentManagement: 'Environment management',
    libraryConfiguration: 'Library Configuration',
    failedToOpenConfig: 'Failed to open Environment Management config',
    successfullyLoaded: 'Successfully loaded Extension Management plugin',
    unableToFetchEnvironment: 'Unable to fetch environment',
    // Config form strings
    condaTitle: 'Python - Conda Packages/Extensions',
    condaDescription1:
      'Use this interface to manage automatic Conda package installations for your environment. Packages specified here will be installed each time your space runs.',
    condaDescription2: 'Enter package names and optional version constraints (e.g., pandas or pandas>=1.0.0)',
    condaDescription3: 'For more information on package specification, see',
    condaLinkText: 'Conda package specification',
    importantNotes: 'Important Notes:',
    note1: '• Closing the background terminal cancels ongoing installations',
    note2:
      '• After package installation, Jupyter server automatically restarts. This restart clears all in-memory variables and active sessions',
    note3:
      '• Removing packages from this interface only prevents future installations. Package uninstallation must be done separately',
    note4:
      '• Channel priorities set here apply only to this interface. Packages installed via notebook or terminal are not tracked here',
    note5: '• Installation requires internet access (except for custom channels)',
    // Error messages
    corruptedConfigTitle: 'The configuration file {path} is corrupted or invalid.',
    corruptedConfigBody:
      'To resolve this issue: • Remove the corrupted file and restart the UI (you will need to reconfigure preferences), OR • Fix the file format back to how it was originally',
    corruptedConfigNote:
      'Note: Removing the file will reset all saved extension and package configurations. Please exit and reopen this widget after making changes.',
    // UI strings
    installInCurrentSession: 'Install in current session',
    saveAllChanges: 'Save all changes',
    saving: 'Saving...',
    resolveErrors: 'You must resolve all errors to save',
    invalidInput: 'Invalid input',
    savedPackageConfigurations: 'Saved package configurations',
    // Schema strings
    packageChannelsTitle: 'Package Channels',
    packageSpecsTitle: 'Package Specifications',
    condaPackagesTitle: 'Conda Packages/Extensions',
    libraryManagementConfiguration: 'Library management configuration',
    // Command Monitor messages
    successfullyInstalledPackages: 'Successfully installed packages and extensions',
    failedToInstallPackages: 'Failed to install packages and extensions',
  },
};
