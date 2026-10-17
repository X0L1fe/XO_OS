import { useEffect, useState } from "react";

export const FILTER_EVENT_NAME = "xo-os:schedule-filters-changed";

/**
 * Возвращает число, которое увеличивается каждый раз,
 * когда пользователь меняет фильтры расписания.
 * Используй его как зависимость в useEffect загрузки данных.
 */
export function useFiltersRefreshKey() {
    const [key, setKey] = useState(0);

    useEffect(() => {
        const handler = () => setKey((value) => value + 1);

        window.addEventListener(FILTER_EVENT_NAME, handler);

        return () => {
            window.removeEventListener(FILTER_EVENT_NAME, handler);
        };
    }, []);

    return key;
}