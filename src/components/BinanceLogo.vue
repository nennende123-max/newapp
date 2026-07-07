<template>
  <svg
    class="binance-logo"
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 126.61 126.61"
    :width="size"
    :height="size"
    aria-label="Binance"
    role="img"
  >
    <g fill="var(--color-accent)">
      <path d="M38.73 53.2l-12.88 12.88L63.3 103.55l37.45-37.45L87.87 53.2 63.3 77.77z" />
      <path d="M38.73 12.88L25.85 25.76 63.3 63.21l37.45-37.45L87.87 12.88 63.3 37.45z" />
      <path d="M12.88 38.73L0 51.61l12.88 12.88L25.76 51.61z" />
      <path d="M113.72 38.73l-12.88 12.88 12.88 12.88 12.88-12.88z" />
    </g>
  </svg>
</template>

<script setup>
defineProps({
  size: {
    type: [Number, String],
    default: 22
  }
});
</script>

<style scoped>
.binance-logo {
  display: block;
  flex-shrink: 0;
}
</style>
