import React from "react";
import { ConfigGroup, Route } from "./types";
import SearchBar from "./components/SearchBar/SearchBar";

type Props = {
  route: Route;
  navigate: (to: Route) => void;
  groups: ConfigGroup[];
};

function Home(props: Props) {
  return (
    <div className="home">
      <div className="home-search-prompt">What do you want to do today?</div>
      <SearchBar
        groups={props.groups}
        navigate={props.navigate}
        route={props.route}
      />
    </div>
  );
}

export default Home;
