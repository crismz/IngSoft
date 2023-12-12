export const createMockEventSource = (cardData) => ({
	addEventListener: (eventName, callback) => {
		if (eventName) {
			// Simulate an event.
			callback({ data: JSON.stringify(cardData) });
		}
	},
});
