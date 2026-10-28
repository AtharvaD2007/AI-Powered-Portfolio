import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';

/**
 * Modern Accessible Dialog component adhering to Modern Web Guidance.
 * Uses native <dialog> element, manages top-layer focus containment,
 * and handles light dismiss cleanly.
 */
export default function Modal({ isOpen, onClose, title, children, maxWidth = '650px' }) {
  const dialogRef = useRef(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    if (isOpen) {
      if (!dialog.open) {
        dialog.showModal();
      }
    } else {
      if (dialog.open) {
        dialog.close();
      }
    }
  }, [isOpen]);

  // Handle native cancel event (Esc key)
  const handleCancel = (e) => {
    e.preventDefault();
    onClose();
  };

  // Handle backdrop click
  const handleBackdropClick = (e) => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    const rect = dialog.getBoundingClientRect();
    const isInDialog = (
      rect.top <= e.clientY &&
      e.clientY <= rect.top + rect.height &&
      rect.left <= e.clientX &&
      e.clientX <= rect.left + rect.width
    );
    if (!isInDialog) {
      onClose();
    }
  };

  return (
    <dialog
      ref={dialogRef}
      onCancel={handleCancel}
      onClick={handleBackdropClick}
      aria-labelledby="dialog-title"
      className="modern-dialog"
      style={{ maxWidth }}
    >
      <div className="dialog-content" onClick={(e) => e.stopPropagation()}>
        <div className="dialog-header">
          <h2 id="dialog-title" className="dialog-title">{title}</h2>
          <button
            type="button"
            className="dialog-close-btn"
            onClick={onClose}
            aria-label="Close dialog"
          >
            <X size={20} />
          </button>
        </div>
        <div className="dialog-body">
          {children}
        </div>
      </div>
    </dialog>
  );
}
