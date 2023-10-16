const throttle = (fn: Function, delay: number) => {
    let timer: any = null;
    let context: any = this;
    return (...args: any) => {
        if (timer) {
            return;
        }
        timer = setTimeout(() => {
            fn.call(context, ...args);
            timer = null;
        }, delay);
    };
}

export default throttle;