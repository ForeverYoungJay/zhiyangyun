<template><ModuleCrudPage title="A1-M6 健康档案" list-url="/m6-health/vitals" create-url="/m6-health/vitals" :fields="fields" :columns="columns" /></template>
<script setup lang="ts">
import ModuleCrudPage from '../../components/ModuleCrudPage.vue'
const fields=[{key:'elder_id',label:'elder_id'},{key:'temperature',label:'temperature'},{key:'systolic',label:'systolic'},{key:'diastolic',label:'diastolic'},{key:'pulse',label:'pulse'}]
const columns=['id','elder_id','temperature','systolic','diastolic','pulse','recorded_at']
</script>
