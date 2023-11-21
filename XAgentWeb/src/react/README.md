# XAgent 的web项目基于vue3 + vite ，且支持React组件

引入方式： 

1. 在Vue组件中创建一个container节点

    ```html
    <div id="react-container" ref="reactContainer"></div>
    ```

2. 在Vue组件中引入react组件

    ```js
    import renderReactCompInsideVue from '@/react-js/index.jsx';

    const reactContainer = ref(null);
    ```

3. 将React组件渲染到container节点中

    ```js
    renderReactCompInsideVue(<YourComponent />, reactContainer.value);
    ```




