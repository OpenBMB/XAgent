<template>
    <div class="image-wrapper">
        <img :src="urlString" />
    </div>
</template>

<script setup lang="ts">

const props = defineProps({
    urlString: {
        type: String,
        required: true
    }
})

const urlString = computed(() => props.urlString)

watch(() => props.urlString, (newVal, oldVal) => {
    console.log(urlString.value)
})
</script>

<style lang="scss" scoped>

.image-wrapper {
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
}

</style>