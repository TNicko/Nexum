import { useState } from "react";

const useLocalStorage = <T>(key: string, initialValue: T) => {
  const [value, setValue] = useState<T>(() => {
		const item = window.localStorage.getItem(key);
		return item ? JSON.parse(item) : initialValue;
	});


	const setAndStoreValue = (newValue: T | ((val: T) => T)) => {
		setValue((currentValue) => {
			const result = newValue instanceof Function ? newValue(currentValue) : newValue;
			window.localStorage.setItem(key, JSON.stringify(result));
			return result;
		})
	}

	return [value, setAndStoreValue] as [T, typeof setAndStoreValue];
};

export default useLocalStorage;
