<template><ModuleCrudPage title="A1-M4 用药管理" list-url="/m4-medication/orders" create-url="/m4-medication/orders" :fields="fields" :columns="columns" /></template>
<script setup lang="ts">
import ModuleCrudPage from '../../components/ModuleCrudPage.vue'
const fields=[{key:'elder_id',label:'elder_id'},{key:'drug_name',label:'drug_name'},{key:'dosage',label:'dosage'},{key:'frequency',label:'frequency'},{key:'start_date',label:'start_date'}]
const columns=['id','elder_id','drug_name','dosage','frequency','start_date','status']
</script>
