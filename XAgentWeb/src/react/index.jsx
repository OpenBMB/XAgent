import React from 'react';
import ReactDOM from 'react-dom/client'

export default function useReactInsideVue (ReactApp, dom) {
    if(!dom) {   
        console.error('Render react component inside vue component error: dom is required');
    } else {
        const _root = ReactDOM.createRoot(dom);
        if(
            ReactApp instanceof Function || 
            ReactApp instanceof React.PureComponent ||
            ReactApp instanceof React.ClassComponent ||
            ReactApp instanceof React.Component) {
            _root.render(<ReactApp />);
        } else {
            try {
                _root.render(ReactApp);
            } catch (error) {
                console.error('Render react component inside vue component error: not a valid react component');
            }
        }
    }
}
