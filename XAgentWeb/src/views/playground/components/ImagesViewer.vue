<template>
    <div class="image-viewer-wrapper" v-if="dataList.length > 0">
        <div class="image-viewer-container" ref="container">
            <ul id="images" 
                class="images-list"
                :class="{'single-file-mode': isSingleFile}"
                >
                <li v-for="(image, index) in images" :key="index" class="image-item">
                    <img 
                        :src="image.data"
                        :alt="'Picture '+ (index + 1)"
                        class="image"
                        :draggable="false"
                    />
                    <span class="image-name">
                        {{  image.name }}
                    </span>
                </li>
            </ul>
        </div>
    </div>
</template>

<script lang="js">

import Viewer from 'viewerjs';
import { ref, onMounted } from 'vue';

export default {
    name: 'ImageViewer',
    props: {
        dataList: {
            type: Array,
            default: () => []
        },
        isSingleFile: {
            type: Boolean,
            default: false,
            required: false
        }
    },
    setup(props) {
        const container = ref(null);
        
        const isSingleFile = computed(() => {
            return props.isSingleFile;
        });

        const images = computed(() => {
            return props.dataList.map((item) => {
                return {
                    name: item.name,
                    data: isSingleFile.value ? 
                        item.data : `data:image/${item.type};base64,${item.data}`
                }
            });
        });

        watch([container, images], () => {
            if (container.value) {
                const viewer = new Viewer(container.value, {
                    inline: false,
                    backdrop: true,
                    navbar: true,
                    toolbar: false,
                    title: true,
                    viewed() {
                        viewer.zoomTo(1);
                    },
                });
            }
        }, {
            immediate: true
        });

        return {
            container,
            images,
        };
    }
}

</script>

<style scoped lang="scss">

@import 'viewerjs/dist/viewer.css';

#images {
    width: 100%;
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    align-items: center;
    list-style: none;
}

.image {
    height: 100px;
    cursor: pointer;
    margin: 5px;
    display: inline-block;
}
.image-viewer-wrapper{
    width: 100% !important;
    height: 100%;
}

.image-viewer-container {
    width: 100% !important;
    height: 100%;
}

.images-list {
    width: 100%;
    height: 100%;
    padding: 0;
    margin: 0;
    list-style: none;
    display: grid;
    grid-template-columns: repeat(
      auto-fill, minmax(130px, 1fr)
    );
    grid-gap: 10px;

    li.image-item {
        height: auto;
        width: auto;
        max-width: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;

        .image-name {
            width: 100%;
            text-align: center;
            margin-top: 5px;
            margin: 5px auto 0 auto;
            color: #999;
        }
    }
}

.single-file-mode {
    display: flex !important;
    justify-content: center !important;
    align-items: center!important;

    li.image-item {
        height: auto;
        width: auto;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;

        image {
            height: auto;
            width: 100%;
        }
    }

    .image-name {
        width: 100%;
        text-align: center;
        margin-top: 5px;
        margin: 5px auto 0 auto;
        color: #fff;
    }
}
</style>
