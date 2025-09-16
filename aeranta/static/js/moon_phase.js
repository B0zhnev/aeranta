function renderMoon(canvas, data) {
    if (!canvas || !canvas.getContext) return;
    data = data || {};
    const ctx = canvas.getContext('2d');

    const w = canvas.width;
    const h = canvas.height;
    const cx = w/2;
    const cy = h/2;
    const r = Math.max(1, Math.min(w,h)/2 - 1);

    const illum = Math.max(0, Math.min(1, (Number(data.moon_illumination_percentage)||0)/100));
    const apiPhase = (data.moon_phase||'').toUpperCase();
    const angle = (Number(data.moon_parallactic_angle)||0) * Math.PI/180;

    // --- новая логика для визуализации ---
    let renderPhase = apiPhase;
    const QUARTER_LOWER = 0.45;
    const QUARTER_UPPER = 0.55;

    if (apiPhase === 'LAST_QUARTER' && illum < QUARTER_LOWER) {
        renderPhase = 'WANING_CRESCENT';
    }
    if (apiPhase === 'FIRST_QUARTER' && illum > QUARTER_UPPER) {
        renderPhase = 'WAXING_GIBBOUS';
    }

    ctx.clearRect(0,0,w,h);

    // фон луны (тёмный диск)
    ctx.beginPath();
    ctx.arc(cx,cy,r,0,Math.PI*2);
    ctx.fillStyle='black';
    ctx.fill();
    ctx.lineWidth=1;
    ctx.strokeStyle='#666';
    ctx.stroke();

    if(illum<=0.001 || renderPhase==='NEW') return;
    if(illum>=0.999 || renderPhase==='FULL'){
        ctx.beginPath();
        ctx.arc(cx,cy,r,0,Math.PI*2);
        ctx.fillStyle='white';
        ctx.fill();
        ctx.stroke();
        return;
    }

    let dir=0;
    if(renderPhase.includes('WAXING')||renderPhase.includes('FIRST')) dir=+1;
    else if(renderPhase.includes('WANING')||renderPhase.includes('LAST')) dir=-1;
    else dir=illum>=0.5 ? +1 : -1;

    ctx.save();
    ctx.translate(cx,cy);
    ctx.rotate(angle);

    // --- Crescents 🌒🌘 ---
    if(renderPhase==='WAXING_CRESCENT'||renderPhase==='WANING_CRESCENT'){
        const crescentDir = renderPhase==='WAXING_CRESCENT'? +1 : -1;
        const shift = r * illum * 1.4;

        ctx.beginPath();
        ctx.arc(0,0,r,0,Math.PI*2);
        ctx.fillStyle='white';
        ctx.fill();

        ctx.beginPath();
        ctx.arc(0,0,r,0,Math.PI*2);
        ctx.clip();

        ctx.beginPath();
        ctx.arc(-crescentDir*shift,0,r,0,Math.PI*2);
        ctx.fillStyle='black';
        ctx.fill();

    } else if(renderPhase.includes('QUARTER') && illum>=QUARTER_LOWER && illum<=QUARTER_UPPER){
        // --- First/Last Quarter с лёгким изгибом ---
        const t = (illum-QUARTER_LOWER)/(QUARTER_UPPER-QUARTER_LOWER); // 0..1
        const bend = (t-0.5)*0.1*r; // слабый изгиб
        const fillDir = renderPhase.includes('FIRST')? +1 : -1;

        ctx.beginPath();
        ctx.arc(0,0,r,0,Math.PI*2);
        ctx.clip();

        ctx.fillStyle='white';
        ctx.beginPath();
        ctx.moveTo(0,-r);
        for(let y=-r;y<=r;y++){
            const x = fillDir*(r + bend*Math.sin(Math.PI*y/(2*r)));
            ctx.lineTo(x,y);
        }
        ctx.lineTo(0,r);
        ctx.closePath();
        ctx.fill();

    } else {
        // --- Gibbous и другие ---
        function overlapArea(d){
            if(d<=0) return Math.PI*r*r;
            if(d>=2*r) return 0;
            const part=2*r*r*Math.acos(d/(2*r));
            const part2=0.5*d*Math.sqrt(Math.max(0,4*r*r-d*d));
            return part-part2;
        }
        const target = illum*Math.PI*r*r;
        let lo=0, hi=2*r;
        for(let i=0;i<40;i++){
            const mid=(lo+hi)/2;
            if(overlapArea(mid)>target) lo=mid; else hi=mid;
        }
        const d=(lo+hi)/2;
        const sunX = dir*d;

        ctx.beginPath();
        ctx.arc(sunX,0,r,0,Math.PI*2);
        ctx.fillStyle='white';
        ctx.fill();
    }

    ctx.restore();

    // контур луны
    ctx.beginPath();
    ctx.arc(cx,cy,r,0,Math.PI*2);
    ctx.lineWidth=1;
    ctx.strokeStyle='#666';
    ctx.stroke();
}

window.renderMoon = renderMoon;

