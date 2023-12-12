import { createBrowserRouter } from "react-router-dom";
import Home from "./views/Home.jsx";
import CreateMatch from "./views/CreateMatch.jsx";
import JoinMatch from "./views/JoinMatch.jsx";
import Lobby from "./views/Lobby.jsx";
import UserAndMatchProvider from "./utils/context/UserAndMatchProvider.jsx";
import Match from "./views/Match.jsx";
import ListMatches from "./views/ListMatches.jsx";
import PositionsProvider from "./utils/context/PositionsProvider.jsx";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Home />,
  },
  {
    path: "/list",
    element: (
      <UserAndMatchProvider>
        <ListMatches />
      </UserAndMatchProvider>
    ),
  },
  {
    path: "/create",
    element: (
      <UserAndMatchProvider>
        <CreateMatch />
      </UserAndMatchProvider>
    ),
  },
  {
    path: "/join/:id",
    element: (
      <UserAndMatchProvider>
        <JoinMatch />
      </UserAndMatchProvider>
    ),
  },
  {
    path: "/lobby/:id",
    element: (
      <UserAndMatchProvider>
        <Lobby />
      </UserAndMatchProvider>
    ),
  },
  {
    path: "/match/:id",
    element: (
      <UserAndMatchProvider>
        <PositionsProvider>
          <Match />
        </PositionsProvider>
      </UserAndMatchProvider>
    ),
  },
]);

export default router;

