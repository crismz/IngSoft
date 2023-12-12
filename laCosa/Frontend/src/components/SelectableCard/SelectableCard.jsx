import { useContext, useEffect } from "react";
import Card from "../Card/Card";
import { TargetContext } from "../../utils/context/TargetProvider";

/**
 * @param {boolean} isSelectable
 * @param {boolean} isSelected
 * @returns {string}
 */
const getButtonStyle = (isSelectable, isSelected) => {
  if (isSelected) return "-translate-y-6";

  if (isSelectable)
    return "hover:border-white hover:bg-black/60 hover:shadow-black/50 hover:shadow-lg hover:scale-105 hover:-translate-y-3 cursor-pointer active:scale-95";

  // !isSelectable && !isSelected.
  return "cursor-not-allowed";
};

const SelectableCard = ({ cardData, isSelected, setSelectedCardData, handContext }) => {
  const buttonStyle = getButtonStyle(cardData.isSelectable, isSelected);
  const { setTargetPositionInfo } = useContext(TargetContext);

  // When a card is changed to be unselectable or unplayable or undisposable, selectedCardData must be null.
  // PD: it's more correct to do it in the HandOfCards event listener.
  //     However, if the backend sends the hand all the time (by mistake or any reason),
  //     then it may fail. We can change it latter, when we know that
  //     the backend is working successfully.
  useEffect(() => {
    setSelectedCardData(null);
  }, [cardData.isSelectable, cardData.isPlayable, cardData.isDisposable]);

  return (
    handContext === "Intercambiables" ? (
    <button
      className={`${buttonStyle} shadoW duration-200 select-none rounded-lg`}
      onClick={
        cardData.isSelectable
          ? () => {
              setSelectedCardData(cardData);
            }
          : null
      }
    >
      <Card cardData={cardData} />
    </button>
    ):(
    <button
      className={`${buttonStyle} shadoW duration-200 select-none rounded-lg`}
      onClick={
        cardData.isSelectable
          ? () => {
              setSelectedCardData(cardData);
              setTargetPositionInfo(cardData.target);
            }
          : null
      }
    >
      <Card cardData={cardData} />
    </button>
  )
  );
};

export default SelectableCard;
