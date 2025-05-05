export type RunResult = { [region: string]: unknown };

export type ConfigParam = {
  name: string;
  default: string | null;
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
