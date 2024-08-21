<script lang="ts">
</script>

<main>
    <div class="circle">
        <div class="segment" style="--angle: 0deg;">

        </div>
        <div class="segment" style="--angle: 120deg;">

        </div>
        <div class="segment" style="--angle: 240deg;">

        </div>
    </div>
</main>

<style>
    .circle {
        width: 200px;
        height: 200px;
        position: relative;
        border-radius: 50%;
        overflow: hidden;
    }

    .segment {
        width: 100%;
        height: 100%;
        position: absolute;
        top: 0;
        left: 0;
        background-color: #ff8585;
        clip-path: polygon(50% 50%, 100% 0%, 100% 100%);
        transform-origin: 50% 50%;
        transform: rotate(var(--angle));
    }

    .segment:nth-child(2) {
        background-color: #ffcc85;
    }

    .segment:nth-child(3) {
        background-color: #1058ff;
    }
</style>
