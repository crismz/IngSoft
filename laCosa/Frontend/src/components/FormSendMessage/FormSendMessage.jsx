import { useCallback, useContext } from "react";
import { UserAndMatchContext } from "../../utils/context/UserAndMatchProvider";
import DisableableButton from "../DisableableButton/DisableableButton";

const FormSendMessage = ({ active }) => {
  const { matchInfo, userInfo } = useContext(UserAndMatchContext);

  const handleSubmitMessage = useCallback(async (e) => {
    e.preventDefault();
    const messageToSend = e.target.elements.inputMessage.value;

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/partidas/${matchInfo.id}/chat`,
        {
          method: "POST",
          body: JSON.stringify({
            id_jugador: userInfo.id,
            mensaje: messageToSend,
          }),
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) throw new Error("Algo ha salido mal...");
    } catch (error) {
      console.error(error);
    }

    // Clear the input field after sending.
    e.target.elements.inputMessage.value = "";
  }, []);

  return (
    <form onSubmit={handleSubmitMessage}>
      <input
        type="text"
        name="inputMessage"
        placeholder="Escribe tu mensaje..."
        className="text-white bg-transparent border-2 border-white my-3 mx-2 focus:outline-none"
        maxLength="150"
        disabled={!active}
        required
      />
      <DisableableButton text="Enviar" disabled={!active} />
    </form>
  );
};

export default FormSendMessage;
