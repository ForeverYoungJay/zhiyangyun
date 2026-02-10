<template><ModuleCrudPage title="B3 运营看板" list-url="/b3-dashboard/metrics" create-url="/b3-dashboard/metrics" :fields="fields" :columns="columns" /></template>
<script setup lang="ts">
import ModuleCrudPage from '../../components/ModuleCrudPage.vue'
const fields=[{key:'metric_date',label:'metric_date'},{key:'occupancy_rate',label:'occupancy_rate'},{key:'revenue',label:'revenue'},{key:'alerts',label:'alerts'}]
const columns=['id','metric_date','occupancy_rate','revenue','alerts']
</script>
