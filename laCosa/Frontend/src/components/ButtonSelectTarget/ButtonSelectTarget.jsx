import { useContext } from "react";
import { TargetContext } from "../../utils/context/TargetProvider";

const ButtonSelectTarget = ({ playerID, canBeTarget, children }) => {
  const { setTargetID } = useContext(TargetContext);

  return (
    <button
      className={canBeTarget ? "cursor-pointer" : "cursor-not-allowed"}
      onClick={canBeTarget ? () => setTargetID(playerID) : null}
    >
      {children}
    </button>
  );
};

export default ButtonSelectTarget;
