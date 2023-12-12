/**
 * @param {string} type
 * @returns {object}
 */
const getColorCardByType = (type) => {
  const dictionaryOfColors = {
    Panico: {
      textColor: "from-pink-700 via-pink-300 to-white",
      bgColor: "from-pink-950/75 via-black/75 to-black/75",
    },
    Contagio: {
      textColor: "from-red-700 via-red-300 to-white",
      bgColor: "from-red-950/75 via-black/75 to-black/75",
    },
    Accion: {
      textColor: "from-lime-950 via-lime-200 to-white",
      bgColor: "from-lime-950/75 via-black/75 to-black/75",
    },
    Defensa: {
      textColor: "from-cyan-700 via-cyan-200 to-white",
      bgColor: "from-cyan-950/75 via-black/70 to-black/70",
    },
    Obstaculo: {
      textColor: "from-yellow-500 via-yellow-200 to-white",
      bgColor: "from-yellow-950/75 via-black/70 to-black/70",
    },
  };

  return (
    dictionaryOfColors[type] ?? {
      textColor: "text-white",
      bgColor: "bg-black/75",
    }
  );
};

const getTargetPositionText = (targetPositionInfo) => {
  const dictionaryOfTargetPositions = {
    any: "Puedes jugarla sobre cualquier jugador",
    self: "Puedes jugarla sobre ti mismo",
    neighbour: "Puedes jugarla sobre tus vecinos",
  };
  return dictionaryOfTargetPositions[targetPositionInfo];
};

const Card = ({ cardData }) => {
  const { textColor, bgColor } = getColorCardByType(cardData.type);

  return (
    <div
      className={`${bgColor} group bg-gradient-to-tl p-4 w-[180px] h-[230px] text-center flex flex-col justify-between gap-1 rounded-lg items-center`}
    >
      {cardData.target && cardData.name !== "La cosa" && (
        <p className="text-white drop-shadow font-fontgood group-hover:opacity-100 opacity-0 absolute -top-14 transition-all w-fit h-fit">
          <span className="line-clamp-6 text-xs bg-black/60 rounded-lg p-2 duration-200">
            Como jugarla: {getTargetPositionText(cardData.target)}
          </span>
        </p>
      )}
      <div className={cardData.name ? "w-full" : ""}>
        <h1
          className={`text-2xl drop-shadow bg-gradient-to-tl bg-clip-text text-transparent ${textColor}`}
        >
          {cardData.name}
        </h1>
        <hr className="my-2" />
      </div>
      <p className="text-white drop-shadow font-fontgood h-full">
        <span className="line-clamp-6 text-sm group-hover:line-clamp-none group-hover:bg-black/60 rounded-lg group-hover:p-[4px] group-hover:shadow duration-200">
          {cardData.effectDescription}
        </span>
      </p>
    </div>
  );
};

export default Card;
