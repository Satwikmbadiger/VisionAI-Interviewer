import { useEffect, useState, useRef } from "react";

export default function Robot({className=""}) {
    const [isMouseIdle, setMouseIdle] = useState(false);
    const idleTimerRef = useRef(null);

    function centerEyes(eyes) {
        eyes.forEach((eye) => {
            const originalCx = parseFloat(eye.getAttribute("data-original-cx")) || parseFloat(eye.getAttribute("cx"));
            const originalCy = parseFloat(eye.getAttribute("data-original-cy")) || parseFloat(eye.getAttribute("cy"));
            eye.setAttribute("cx", originalCx);
            eye.setAttribute("cy", originalCy);
        });
    }

    function resetIdleTimer(eyes) {
        clearTimeout(idleTimerRef.current);
        idleTimerRef.current = setTimeout(() => {
            centerEyes(eyes);
            setMouseIdle(true);
        }, 3000);
    }

    function moveEyes(e) {
        if (isMouseIdle) {
            setMouseIdle(false);
        }

        const eyes = document.querySelectorAll(".eye");
        const mouseX = e.clientX;
        const mouseY = e.clientY;

        eyes.forEach((eye) => {
            const originalCx =
                parseFloat(eye.getAttribute("data-original-cx")) ||
                parseFloat(eye.getAttribute("cx"));
            const originalCy =
                parseFloat(eye.getAttribute("data-original-cy")) ||
                parseFloat(eye.getAttribute("cy"));

            if (!eye.getAttribute("data-original-cx")) {
                eye.setAttribute("data-original-cx", originalCx);
                eye.setAttribute("data-original-cy", originalCy);
            }

            const svg = eye.closest("svg");
            if (!svg) return;

            const pt = svg.createSVGPoint();
            pt.x = mouseX;
            pt.y = mouseY;
            const svgP = pt.matrixTransform(svg.getScreenCTM().inverse());

            const deltaX = svgP.x - originalCx;
            const deltaY = svgP.y - originalCy;
            const angle = Math.atan2(deltaY, deltaX);

            const maxDistance = 8;
            const actualDistance = Math.sqrt(deltaX ** 2 + deltaY ** 2);
            const distance = Math.min(maxDistance, actualDistance / 8);

            const pupilX = originalCx + Math.cos(angle) * distance;
            const pupilY = originalCy + Math.sin(angle) * distance;

            eye.setAttribute("cx", pupilX);
            eye.setAttribute("cy", pupilY);
        });
        resetIdleTimer(eyes);
    }

    useEffect(() => {
        document.body.addEventListener("mousemove", moveEyes);
        const eyes = document.querySelectorAll(".eye");
        resetIdleTimer(eyes);

        return () => {
            document.body.removeEventListener("mousemove", moveEyes);
            clearTimeout(idleTimerRef.current);
        };
    }, []);

    return (
        <div className={`flex items-center justify-center min-h-screen bg-gradient-to-b ${className}`}>
            <svg width="500" height="600" viewBox="0 0 500 600">
                <defs>
                    <linearGradient id="bodyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#FFFFFF" />
                        <stop offset="50%" stopColor="#F5F5F5" />
                        <stop offset="100%" stopColor="#E8E8E8" />
                    </linearGradient>
                    <radialGradient id="shine">
                        <stop offset="0%" stopColor="#FFFFFF" stopOpacity="0.6" />
                        <stop offset="100%" stopColor="#FFFFFF" stopOpacity="0" />
                    </radialGradient>
                    <filter id="softShadow">
                        <feGaussianBlur in="SourceAlpha" stdDeviation="4"/>
                        <feOffset dx="0" dy="6" result="offsetblur"/>
                        <feComponentTransfer>
                            <feFuncA type="linear" slope="0.3"/>
                        </feComponentTransfer>
                        <feMerge>
                            <feMergeNode/>
                            <feMergeNode in="SourceGraphic"/>
                        </feMerge>
                    </filter>
                </defs>

                <g filter="url(#softShadow)">
                    {/* Main body - egg shape like EVE */}
                    <path d="M 250 150
                   Q 350 150, 380 250
                   Q 390 320, 380 400
                   Q 360 480, 250 500
                   Q 140 480, 120 400
                   Q 110 320, 120 250
                   Q 150 150, 250 150 Z"
                          fill="url(#bodyGrad)"
                          stroke="#D0D0D0"
                          strokeWidth="2"/>

                    {/* Shine/gloss on body */}
                    <ellipse cx="220" cy="220" rx="80" ry="100" fill="url(#shine)" />

                    {/* Black face screen */}
                    <rect x="150" y="200" width="200" height="90" rx="45" fill="#0a0a0a" />

                    {/* Blue glowing eye displays */}
                    <rect x="170" y="220" width="70" height="50" rx="25" fill="#00BFFF">
                        <animate attributeName="fill" values="#00BFFF;#00D5FF;#00BFFF" dur="3s" repeatCount="indefinite" />
                    </rect>
                    <rect x="260" y="220" width="70" height="50" rx="25" fill="#00BFFF">
                        <animate attributeName="fill" values="#00BFFF;#00D5FF;#00BFFF" dur="3s" repeatCount="indefinite" />
                    </rect>

                    {/* Eye highlights */}
                    <ellipse cx="190" cy="232" rx="18" ry="12" fill="#FFFFFF" opacity="0.5" />
                    <ellipse cx="280" cy="232" rx="18" ry="12" fill="#FFFFFF" opacity="0.5" />

                    {/* Pupils that track mouse */}
                    <ellipse className="eye" cx="205" cy="245" rx="14" ry="18" fill="#001a33" />
                    <ellipse className="eye" cx="295" cy="245" rx="14" ry="18" fill="#001a33" />

                    {/* Arms - small and tucked */}
                    <ellipse cx="100" cy="320" rx="25" ry="45" fill="url(#bodyGrad)" stroke="#D0D0D0" strokeWidth="2" />
                    <ellipse cx="400" cy="320" rx="25" ry="45" fill="url(#bodyGrad)" stroke="#D0D0D0" strokeWidth="2" />

                    {/* Small light on chest */}
                    <circle cx="250" cy="380" r="8" fill="#00BFFF" opacity="0.8">
                        <animate attributeName="opacity" values="0.5;1;0.5" dur="1.5s" repeatCount="indefinite" />
                    </circle>
                </g>
            </svg>
        </div>
    );
}