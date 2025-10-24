import React, { useState, useRef, useEffect } from 'react';

const CustomImageZoom = ({ src, alt, className }) => {
    const [isZoomed, setIsZoomed] = useState(false);
    const [zoomPosition, setZoomPosition] = useState({ x: 0, y: 0 });
    const [imageLoaded, setImageLoaded] = useState(false);
    const [zoomScale, setZoomScale] = useState(2);
    const imageRef = useRef();
    const containerRef = useRef();

    useEffect(() => {
        if (imageLoaded && imageRef.current && containerRef.current) {
            const img = imageRef.current;
            const container = containerRef.current;

            const containerWidth = container.offsetWidth;
            const containerHeight = container.offsetHeight;
            const scaleX = img.naturalWidth / containerWidth;
            const scaleY = img.naturalHeight / containerHeight;

            const optimalScale = Math.max(1.5, Math.min(Math.max(scaleX, scaleY), 4));
            setZoomScale(optimalScale);
        }
    }, [imageLoaded]);

    const handleMouseMove = (e) => {
        if (!isZoomed || !containerRef.current) return;

        const container = containerRef.current;
        const rect = container.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;

        setZoomPosition({ x, y });
    };

    const handleMouseEnter = () => {
        setIsZoomed(true);
    };

    const handleMouseLeave = () => {
        setIsZoomed(false);
    };

    const handleImageLoad = () => {
        setImageLoaded(true);
    };

    return (
        <div
            ref={containerRef}
            className={`relative overflow-hidden cursor-zoom-in ${className}`}
            onMouseMove={handleMouseMove}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
        >
            <img
                ref={imageRef}
                src={src}
                alt={alt}
                className={`w-full h-full object-cover transition-transform duration-200 ${isZoomed ? 'cursor-zoom-out' : 'cursor-zoom-in'
                    }`}
                style={{
                    transform: isZoomed
                        ? `scale(${zoomScale})`
                        : 'scale(1)',
                    transformOrigin: `${zoomPosition.x}% ${zoomPosition.y}%`,
                }}
                onLoad={handleImageLoad}
                onError={(e) => {
                    e.target.src = '/placeholder-image.jpg';
                }}
            />
        </div>
    );
};

export default CustomImageZoom;