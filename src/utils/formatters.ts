
export const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(0) + 'K';
  }
  return num.toLocaleString();
};

export const formatDateTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit' 
  });
};

export const formatTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleTimeString([], { 
    hour: '2-digit', 
    minute: '2-digit',
    hour12: true
  });
};

export const formatCompactDateTime = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const isToday = date.toDateString() === now.toDateString();
  
  if (isToday) {
    return date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false
    });
  } else {
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const time = date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false
    });
    return `${month}/${day} ${time}`;
  }
};
