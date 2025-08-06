import React from 'react';

const prompts = [
  '"Automate my email workflow"',
  '"Scrape product data"',
  '"Process CSV files"'
];

interface PromptGalleryProps {
  onPromptSelect?: (prompt: string) => void;
}

export const PromptGallery: React.FC<PromptGalleryProps> = ({ onPromptSelect }) => {
  return (
    <div className="px-4 py-3">
      <h2 className="text-sm font-medium text-gray-700 mb-3">Prompt Gallery</h2>
      <div className="space-y-2">
        {prompts.map((prompt, index) => (
          <button
            key={index}
            onClick={() => onPromptSelect?.(prompt.replace(/"/g, ''))}
            className="block w-full text-left text-sm text-gray-600 hover:text-blue-600 transition-colors"
          >
            {prompt}
          </button>
        ))}
      </div>
    </div>
  );
};