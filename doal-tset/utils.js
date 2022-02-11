export const sleepNow = (delay) =>
  new Promise((resolve) => setTimeout(resolve, delay));

export const jsonLog = (obj) => console.log(JSON.stringify(obj));
