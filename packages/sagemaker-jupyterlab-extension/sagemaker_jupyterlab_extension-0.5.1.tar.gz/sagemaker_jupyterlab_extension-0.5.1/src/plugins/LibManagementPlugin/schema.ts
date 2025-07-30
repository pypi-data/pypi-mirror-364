import { JSONSchema7 } from 'json-schema';
import { VALID_NAME_PATTERN, il18Strings } from '../../constants';

// JSON schema for conda package specifications
const CONDA_PACKAGE_SPECIFICATION_SCHEMA: JSONSchema7 = {
  type: 'string',
  pattern: VALID_NAME_PATTERN,
};

// JSON schema for conda channels
const CONDA_CHANNEL_SCHEMA: JSONSchema7 = {
  type: 'string',
  pattern: VALID_NAME_PATTERN,
};

/**
 * JSON schema for the entire library configuration file
 * Defines the structure and validation rules for .libs.json
 */
export const LIBRARY_CONFIG_SCHEMA: JSONSchema7 = {
  title: il18Strings.LibManagement.libraryManagementConfiguration,
  description: il18Strings.LibManagement.libraryManagementConfiguration,
  type: ['object', 'null'],
  properties: {
    Python: {
      type: 'object',
      title: 'Python',
      properties: {
        CondaPackages: {
          title: il18Strings.LibManagement.condaPackagesTitle,
          type: ['object', 'null'],
          properties: {
            Channels: {
              title: il18Strings.LibManagement.packageChannelsTitle,
              type: ['array', 'null'],
              items: CONDA_CHANNEL_SCHEMA,
            },
            PackageSpecs: {
              title: il18Strings.LibManagement.packageSpecsTitle,
              type: ['array', 'null'],
              items: CONDA_PACKAGE_SPECIFICATION_SCHEMA,
            },
          },
        },
      },
    },
  },
};
