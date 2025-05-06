export type RunResult = {
  results: {
    [regionName: string]: unknown;
  };
  errors: {
    [regionName: string]: RegionError;
  }
}

export interface RegionError {
  type: string;
  message: string;
  status_code: number;
}

export type ConfigParam = {
  name: string;
  default: string | null;
  type: 'text' | 'textarea' | 'select' | 'number' | 'integer';
  enumValues: string[] | null;
};

export interface ConfigFunction {
  name: string;
  source: string;
  docstring: string;
  parameters: ConfigParam[];
  isReadonly: boolean;
}

export interface MarkdownFile {
  name: string,
  content: string;
}

export interface ConfigGroup {
  group: string;
  functions: ConfigFunction[];
  docstring: string;
  markdownFiles: MarkdownFile[];
}

export interface Config {
  title: string;
  regions: string[];
  groups: ConfigGroup[];
  groupsWithoutAccess: string[];
}

interface HomeRoute {
  regions: string[];
}

interface GroupRoute {
  regions: string[];
  group: string;
}

interface ScriptRoute {
  regions: string[];
  group: string;
  function: string;
}

export type Route = HomeRoute | GroupRoute | ScriptRoute;


export type RowData = {
  [key: string]: unknown;
}

export type MergedRowData = {
  region: string;
  [key: string]: unknown;
}
