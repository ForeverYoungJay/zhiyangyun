<template><ModuleCrudPage title="A2-OA1 排班" list-url="/oa1-shift/templates" create-url="/oa1-shift/templates" :fields="fields" :columns="columns" /></template>
<script setup lang="ts">
import ModuleCrudPage from '../../components/ModuleCrudPage.vue'
const fields=[{key:'name',label:'name'},{key:'start_time',label:'start_time'},{key:'end_time',label:'end_time'}]
const columns=['id','name','start_time','end_time']
</script>
