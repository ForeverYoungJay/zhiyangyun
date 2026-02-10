<template><ModuleCrudPage title="A1-M5 膳食管理" list-url="/m5-meal/plans" create-url="/m5-meal/plans" :fields="fields" :columns="columns" /></template>
<script setup lang="ts">
import ModuleCrudPage from '../../components/ModuleCrudPage.vue'
const fields=[{key:'name',label:'name'},{key:'plan_date',label:'plan_date'},{key:'meal_type',label:'meal_type'},{key:'nutrition_tag',label:'nutrition_tag'}]
const columns=['id','name','plan_date','meal_type','nutrition_tag']
</script>
