import { useEffect } from 'react';

export const GlowCursor: React.FC = () => {
  useEffect(() => {
    const glow = document.createElement('div');
    glow.id = 'glow-cursor';
    Object.assign(glow.style, {
      position: 'fixed',
      top: '0',
      left: '0',
      width: '300px',
      height: '300px',
      borderRadius: '50%',
      background: 'radial-gradient(circle, rgba(0,168,255,0.07) 0%, transparent 70%)',
      pointerEvents: 'none',
      zIndex: '9999',
      transform: 'translate(-50%, -50%)',
      transition: 'opacity 0.3s ease',
      opacity: '0',
    });
    document.body.appendChild(glow);

    const onMove = (e: MouseEvent) => {
      glow.style.left = `${e.clientX}px`;
      glow.style.top = `${e.clientY}px`;
      glow.style.opacity = '1';
    };

    const onLeave = () => {
      glow.style.opacity = '0';
    };

    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseleave', onLeave);

    return () => {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseleave', onLeave);
      glow.remove();
    };
  }, []);

  return null;
};
