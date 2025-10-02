import { useEffect } from 'react';
import { Redirect, router } from 'expo-router';
import AsyncStorage from '@react-native-async-storage/async-storage';

const USER_PHOTO_KEY = 'uplo5_user_photo';

export default function Index() {
  useEffect(() => {
    checkUserPhoto();
  }, []);

  const checkUserPhoto = async () => {
    try {
      const userPhoto = await AsyncStorage.getItem(USER_PHOTO_KEY);
      if (userPhoto) {
        router.replace('/(main)/feed');
      } else {
        router.replace('/onboarding');
      }
    } catch (error) {
      console.error('[INDEX] Error checking user photo:', error);
      router.replace('/onboarding');
    }
  };

  return null;
}
