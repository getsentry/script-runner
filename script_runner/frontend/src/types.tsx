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
  type: "read" | "write";
}

export interface ConfigGroup {
  group: string;
  functions: ConfigFunction[];
  docstring: string;
}

export interface Config {
  title: string;
  regions: string[];
  groups: ConfigGroup[];
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
