<template><ModuleCrudPage title="A1-M7 费用管理" list-url="/m7-billing/items" create-url="/m7-billing/items" :fields="fields" :columns="columns" /></template>
<script setup lang="ts">
import ModuleCrudPage from '../../components/ModuleCrudPage.vue'
const fields=[{key:'elder_id',label:'elder_id'},{key:'item_name',label:'item_name'},{key:'amount',label:'amount'},{key:'charged_on',label:'charged_on'}]
const columns=['id','elder_id','item_name','amount','charged_on','status']
</script>
