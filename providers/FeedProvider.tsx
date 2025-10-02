import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { FeedLoadingService, FeedEntry } from '../lib/FeedLoadingService';

const USER_PHOTO_KEY = 'uplo5_user_photo';

interface FeedContextType {
  feed: FeedEntry[];
  currentIndex: number;
  setCurrentIndex: (index: number) => void;
  workerStats: { active: number; max: number; bufferHealth: number };
  isReady: boolean;
}

const FeedContext = createContext<FeedContextType | null>(null);

export function FeedProvider({ children }: { children: React.ReactNode }) {
  const [feed, setFeed] = useState<FeedEntry[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isReady, setIsReady] = useState(false);
  const [workerStats, setWorkerStats] = useState({ active: 0, max: 30, bufferHealth: 0 });

  const loadingServiceRef = useRef<FeedLoadingService | null>(null);
  const userPhotoRef = useRef<string | null>(null);
  const updateIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize service and load user photo
  useEffect(() => {
    const initialize = async () => {
      try {
        // Load user photo
        const userPhoto = await AsyncStorage.getItem(USER_PHOTO_KEY);
        if (!userPhoto) {
          console.error('[FEED-PROVIDER] No user photo found');
          return;
        }

        userPhotoRef.current = userPhoto;
        loadingServiceRef.current = new FeedLoadingService();

        // Initialize feed with first 50 positions
        const initialPositions = Array.from({ length: 50 }, (_, i) => i);
        loadingServiceRef.current.addJobs(initialPositions);

        // Start processing queue
        loadingServiceRef.current.processQueue(userPhoto);

        setIsReady(true);

        // Start update loop
        updateIntervalRef.current = setInterval(() => {
          if (loadingServiceRef.current) {
            const stats = loadingServiceRef.current.getWorkerStats();
            setWorkerStats(stats);

            // Update feed entries
            const positions = Array.from({ length: currentIndex + 30 }, (_, i) => i);
            const entries = loadingServiceRef.current.getEntries(positions);
            setFeed(entries);
          }
        }, 500);

      } catch (error) {
        console.error('[FEED-PROVIDER] Initialization error:', error);
      }
    };

    initialize();

    return () => {
      if (updateIntervalRef.current) {
        clearInterval(updateIntervalRef.current);
      }
    };
  }, []);

  // Handle index changes and trigger new jobs
  useEffect(() => {
    if (!loadingServiceRef.current || !userPhotoRef.current) return;

    // Add jobs for next 30 positions
    const nextPositions = Array.from(
      { length: 30 },
      (_, i) => currentIndex + i
    );
    loadingServiceRef.current.addJobs(nextPositions);

    // Process queue
    loadingServiceRef.current.processQueue(userPhotoRef.current);

  }, [currentIndex]);

  const value: FeedContextType = {
    feed,
    currentIndex,
    setCurrentIndex,
    workerStats,
    isReady
  };

  return (
    <FeedContext.Provider value={value}>
      {children}
    </FeedContext.Provider>
  );
}

export function useFeed() {
  const context = useContext(FeedContext);
  if (!context) {
    throw new Error('useFeed must be used within FeedProvider');
  }
  return context;
}
