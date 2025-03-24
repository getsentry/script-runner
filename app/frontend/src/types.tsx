export type RunResult = { [region: string]: unknown };

export type ConfigParam = { name: string, default: string | null, enumValues: string[] | null };

export interface ConfigFunction {
  name: string,
  source: string,
  docstring: string,
  parameters: ConfigParam[],
}

export interface ConfigGroup {
  group: string;
  functions: ConfigFunction[];
}

export interface Config {
  regions: string[],
  groups: ConfigGroup[],
  executableGroups: string[],
}

interface HomeRoute {
  regions: string[]
}

interface GroupRoute {
  regions: string[],
  group: string,
}

interface ScriptRoute {
  regions: string[],
  group: string,
  function: string,
}


export type Route = HomeRoute | GroupRoute | ScriptRoute;
