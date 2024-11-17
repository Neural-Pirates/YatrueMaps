

// Assuming posts is an array that is defined somewhere in your code
let recentThreads: any[] = []

export const getRecentThread = () => recentThreads;

export const setRecentThread = (thread: any) => {
    recentThreads.unshift(thread);
    console.log("Thead updated:", recentThreads);
};

