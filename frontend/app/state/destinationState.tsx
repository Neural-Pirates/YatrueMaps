import { useState, useCallback } from 'react';

export function useDestination() {
  const [destination, setDestination] = useState<number[] | null>([78.4867, 17.3850]); // Default to a valid coordinate

  const updateDestination = useCallback((newDestination: number[]) => {
    setDestination((prevDestination) =>
      JSON.stringify(prevDestination) !== JSON.stringify(newDestination)
        ? newDestination
        : prevDestination
    );
  }, []);

  return { destination, updateDestination };
}
