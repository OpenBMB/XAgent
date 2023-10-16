const debounce = (fn: Function, delay: number) => {
    let timer: any = null;
    let context:any = this;
    return (...args: any) => {
        if (timer) {
            clearTimeout(timer);
        } 
        timer = setTimeout(() => {
            fn.call(context, ...args);
        }, delay);
    };
}

export default debounce;