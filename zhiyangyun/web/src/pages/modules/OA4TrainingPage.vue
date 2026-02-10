<template><ModuleCrudPage title="A2-OA4 培训" list-url="/oa4-training/courses" create-url="/oa4-training/courses" :fields="fields" :columns="columns" /></template>
<script setup lang="ts">
import ModuleCrudPage from '../../components/ModuleCrudPage.vue'
const fields=[{key:'title',label:'title'},{key:'category',label:'category'},{key:'required_score',label:'required_score'}]
const columns=['id','title','category','required_score','status']
</script>
