import { LabIcon } from '@jupyterlab/ui-components';
import React from 'react';

import libraryIconStr from './icons/md-library-icon.svg';
import condaIconStr from './icons/conda-icon.svg';
import { StyledLink, ErrorText, ImportantNote } from './styles';
import { CONNECTION_TYPE, il18Strings } from '../../constants';

export { initConfig } from '../../constants';

// Icon for the library management plugin
export const libMgmtIcon = new LabIcon({
  name: 'libmgmt:library-management-icon',
  svgstr: libraryIconStr,
});

// Icon for conda packages
export const condaIcon = new LabIcon({
  name: 'libmgmt:conda-icon',
  svgstr: condaIconStr,
});

/**
 * Configuration metadata for different package types
 * Defines UI elements and supported connection types
 */
export const CONFIGS: { [key: string]: { [key: string]: ConfigMetadata } } = {
  Python: {
    CondaPackages: {
      title: il18Strings.LibManagement.condaTitle,
      icon: condaIcon,
      supportedConnectionType: [CONNECTION_TYPE.IAM],
      // https://docs.conda.io/projects/conda-build/en/latest/resources/package-spec.html
      additionalDescription: [
        <div key="conda-desc-1">{il18Strings.LibManagement.condaDescription1}</div>,
        <div key="conda-desc-2">{il18Strings.LibManagement.condaDescription2}</div>,
        <div key="conda-desc-3">
          {il18Strings.LibManagement.condaDescription3}&nbsp;
          {link(
            il18Strings.LibManagement.condaLinkText,
            'https://docs.conda.io/projects/conda-build/en/latest/resources/package-spec.html',
          )}
        </div>,
        <ImportantNote key="conda-desc-4">{il18Strings.LibManagement.importantNotes}</ImportantNote>,
        <div key="conda-desc-5">{il18Strings.LibManagement.note1}</div>,
        <div key="conda-desc-6">{il18Strings.LibManagement.note2}</div>,
        <div key="conda-desc-7">{il18Strings.LibManagement.note3}</div>,
        <div key="conda-desc-8">{il18Strings.LibManagement.note4}</div>,
        <div key="conda-desc-9">{il18Strings.LibManagement.note5}</div>,
      ],
    },
  },
};

/**
 * Metadata interface for configuration items
 * Defines the structure of configuration entries in the UI
 */
export interface ConfigMetadata {
  title: string;
  icon: LabIcon;
  supportedConnectionType: CONNECTION_TYPE[];
  regex?: string;
  additionalDescription?: JSX.Element[];
}

// Error messages displayed to users
export const ERROR_MESSAGES = {
  CORRUPTED_CONFIG_FILE: (path: string) => (
    <>
      <ErrorText>
        {il18Strings.LibManagement.corruptedConfigTitle.replace('{path}', path)}
        <br />
        <br />
        {il18Strings.LibManagement.corruptedConfigBody}
        <br />
        <br />
        {il18Strings.LibManagement.corruptedConfigNote}
      </ErrorText>
    </>
  ),
};

// Helper function to create styled links
function link(linkName: string, href: string) {
  return <StyledLink href={href}>{linkName}</StyledLink>;
}
