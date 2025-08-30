addEventListener("DOMContentLoaded", () => {
    let zIndex = 1;
    let disappearAnimationBusy = false;

    document.querySelectorAll(".card-img-top").forEach((img, i) => {
        /* // for introduction spin
        const duration = (i + 5) * 400;
        img.style.animationDuration = `${duration}ms`;
        setTimeout(() => {
            img.style.animationDuration = "";
            img.classList.remove("introduction-spin");
        }, duration);
        */

        // for click spin
        img.addEventListener("mousedown", () => {
            if (img.classList.contains("click-spin")) return;

            img.style.zIndex = (zIndex++).toString();
            img.classList.add("click-spin");
            setTimeout(() => img.classList.remove("click-spin"), 3000);
        });
    });

    // for disappear spin
    document.querySelectorAll(".card").forEach(card => {
        card.querySelectorAll(".card-body a").forEach(a => {
            a.addEventListener("click", e => {
                e.preventDefault();

                if (disappearAnimationBusy) return;
                disappearAnimationBusy = true;
    
                card.classList.add("disappear-spin");
                setTimeout(() => location.href = a.href, 2000);
            });
        });
    });
});
