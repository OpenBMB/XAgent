<template>
    <div class="nb-previewer">
        <div class="main-nb-previewer-wrapper">
            <div class="main-nb-previewer">
                <div id="notebook-container" ref="notebookContainer"></div>
            </div>
        </div>        
    </div>

</template>

<script lang="js" setup>

import { ref, onMounted, watch } from 'vue'

const props = defineProps({
    datasource: {
        type: Object,
        required: true,
        default: () => ({})
    }
})

const notebookContainer = ref(null)

onMounted(() => {
    window.render_notebook = function (container, ipynb_json) {
        var notebook = window.nb.parse(ipynb_json);
        while (container.hasChildNodes()) {
            container.removeChild(container.lastChild);
        }
        container.appendChild(notebook.render());
        window.Prism.highlightAll();
    };

    window.load_nb_file = function (file) {
        if(!file) return;
        window.render_notebook(notebookContainer.value, file);
    };

});

watch(() => props.datasource, (newVal) => {
    if(window && window.load_nb_file && Object.keys(newVal).length > 0) {
        window.load_nb_file(newVal);
    }
});


</script>

<style scoped lang="scss">

.nb-previewer {
    width: 100%;
    height: 100%;
    padding: 0;
    margin: 0;
}


#notebook-container {
    height: auto;
}

.main-nb-previewer {
    width: 100%;
    height: auto;
    margin-left: 110px;

}

.main-nb-previewer-wrapper {
    width: 100%;
    height: 100%;
    background-color: #fff;
    padding: 0;
    margin: 0;
    padding-top: 30px;
    overflow-x: hidden;
    overflow-y: auto;
}

</style>