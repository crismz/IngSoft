/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,jsx}'],
	theme: {
		extend: {
			backgroundImage: {
				theThing: 'url(/images/background.jpg)',
			},
			fontFamily: {
				fontgood: ['Embrace_The_Blush', 'sans'],
			},
			transitionProperty: {
				BlurAndOpacity: 'filter, opacity',
			},
		},
	},
	plugins: [],
};
