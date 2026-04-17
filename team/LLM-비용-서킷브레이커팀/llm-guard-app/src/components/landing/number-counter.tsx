'use client';

import { useEffect, useRef } from 'react';
import { motion, useMotionValue, useTransform } from 'framer-motion';

interface NumberCounterProps {
  value: number;
  duration?: number;
  prefix?: string;
  suffix?: string;
  className?: string;
}

export function NumberCounter({
  value,
  duration = 2.5,
  prefix = '',
  suffix = '',
  className = '',
}: NumberCounterProps) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, Math.round);
  const isVisible = useRef(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !isVisible.current) {
          isVisible.current = true;
          count.set(value);
        }
      },
      { threshold: 0.5 }
    );

    const div = document.querySelector(`[data-counter-id="${value}"]`);
    if (div) observer.observe(div);

    return () => observer.disconnect();
  }, [value, count]);

  return (
    <motion.span
      data-counter-id={value}
      className={className}
      animate={{
        transition: { duration },
      }}
    >
      <motion.span>
        {rounded}
      </motion.span>
      <span>{suffix || ''}</span>
    </motion.span>
  );
}
