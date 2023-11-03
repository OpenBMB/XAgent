// const throttle = (fn: Function, delay: number) => {
//     let timer: any = null;
//     let context: any = this;
//     return (...args: any) => {
//         if (timer) {
//             return;
//         }
//         timer = setTimeout(() => {
//             fn.call(context, ...args);
//             timer = null;
//         }, delay);
//     };
// } 
// Throttle based on timer

const throttle = (fn: Function, delay: number) => {
    let prev = Date.now();
    let context: any = this;
    return (...args: any) => {
        let now = Date.now();
        if (now - prev >= delay) {
            fn.call(context, ...args);
            prev = Date.now();
        }
    };
}
// Throttle based on time

export default throttle;