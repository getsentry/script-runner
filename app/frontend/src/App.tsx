
import { useEffect, useState, useMemo } from 'react';

import './App.css'
import Home from './Home.tsx'
import Scripts from './Scripts.tsx'
import Script from './Script.tsx'
import Nav from './Nav.tsx'
import { Config, Route } from './types.tsx'
import Header from './Header.tsx'
import NotFound from './NotFound.tsx'
import Api from './api.tsx'

function App() {
  const [route, setRoute] = useState<Route | null>(null);
  const [config, setConfig] = useState<Config | null>(null);
  const api = useMemo(() => {
    return new Api();
  }, []);



  // Run once on app load to parse the initial hash and set route
  useEffect(() => {
    parseHashAndSetRoute();

    window.addEventListener('hashchange', parseHashAndSetRoute);

    return () => {
      window.removeEventListener('hashchange', parseHashAndSetRoute);
    };
  }, []);

  useEffect(() => {
    api.getConfig()
      .then((data: Config) => {
        setConfig(data);
      })
      .then(() => {
        parseHashAndSetRoute();
      })
  }, [api])

  const parseHashAndSetRoute = () => {
    const hash = window.location.hash.slice(1);
    const pathAndQuery = hash.split('?');
    const regions = [];

    if (pathAndQuery.length > 1) {
      regions.push(...pathAndQuery[1].split('&').map(q => q.split('=')[1]));
    }

    const path = pathAndQuery[0];
    const fragments = path.split('/').filter(i => i.length !== 0);

    let route;
    switch (fragments.length) {
      case 1:
        route = { "regions": regions, "group": fragments[0] }
        break;
      case 2:
        route = { "regions": regions, "group": fragments[0], "function": fragments[1] }
        break;
      default:
        route = { "regions": regions }
    }
    setRoute(route);
  };


  useEffect(() => {
    let hash = "";

    if (route === null) {
      return;
    }

    if ("group" in route) {
      hash += `${route.group}`
    }
    if ("function" in route) {
      hash += `/${route.function}`
    }

    if (route.regions.length > 0) {
      hash += `?${route.regions.map(region => `region=${encodeURIComponent(region)}`).join('&')}`;
    }

    window.location.hash = hash;
  }, [route]);

  function execute(regions: string[], group: string, func: string, parameters: string[]) {
    return api.run({
      'group': group,
      'function': func,
      'parameters': parameters,
      'regions': regions,
    })
  }

  function navigate(to: Route) {
    setRoute(to)

    let hash: string;

    if ("function" in to) {
      hash = `${to.group}/${to.function}`
    } else if ("group" in to) {
      hash = to.group
    } else {
      hash = ''
    }

    const querystring = `${to.regions.map(region => `region=${encodeURIComponent(region)}`).join('&')}`;

    if (querystring.length > 0) {
      hash += `?${querystring}`;
    }
    window.location.hash = hash;

  }

  function getActiveComponent() {
    if (!config || route === null) {
      return;
    }

    if ("function" in route) {
      const group = config.groups.find(g => g.group == route.group);

      if (!group) {
        return <NotFound />
      }

      const functionDef = group.functions.find(f => f.name == route.function);

      if (!functionDef) {
        return <NotFound />
      }

      return <Script regions={route.regions} group={route.group} function={functionDef} execute={execute} canExecute={config.executableGroups.includes(route.group)} />
    }

    if ("group" in route) {
      const group = config.groups.find(g => g.group == route.group);
      if (group) {
        return <Scripts regions={route.regions} group={group} navigate={navigate} />
      } else {
        return <NotFound />
      }

    }

    return <Home groups={config.groups} route={route} navigate={navigate} />

  }

  if (route === null || config === null) {
    return;
  }


  return (
    <>
      <Header regions={config.regions} route={route} navigate={navigate} />
      <div className="page-container">
        <Nav navigate={navigate} groups={config.groups} route={route} />
        <div className="content">
          {config.groups.length && getActiveComponent()}
        </div>
      </div>
    </>
  )
}

export default App
