<template><ModuleCrudPage title="B1 小程序服务请求" list-url="/b1-miniapp/requests" create-url="/b1-miniapp/requests" :fields="fields" :columns="columns" /></template>
<script setup lang="ts">
import ModuleCrudPage from '../../components/ModuleCrudPage.vue'
const fields=[{key:'elder_id',label:'elder_id'},{key:'request_type',label:'request_type'},{key:'content',label:'content'}]
const columns=['id','elder_id','request_type','content','status']
</script>
