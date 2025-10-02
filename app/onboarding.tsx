import { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Image,
  StyleSheet,
  Dimensions,
  Alert
} from 'react-native';
import { router } from 'expo-router';
import * as ImagePicker from 'expo-image-picker';
import AsyncStorage from '@react-native-async-storage/async-storage';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');
const USER_PHOTO_KEY = 'uplo5_user_photo';

export default function Onboarding() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const pickImage = async () => {
    const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();

    if (!permissionResult.granted) {
      Alert.alert(
        'Permission Required',
        'Please allow access to your photo library to continue.'
      );
      return;
    }

    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      aspect: [3, 4],
      quality: 0.8,
    });

    if (!result.canceled && result.assets[0]) {
      setSelectedImage(result.assets[0].uri);
    }
  };

  const takePhoto = async () => {
    const permissionResult = await ImagePicker.requestCameraPermissionsAsync();

    if (!permissionResult.granted) {
      Alert.alert(
        'Permission Required',
        'Please allow camera access to take a photo.'
      );
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [3, 4],
      quality: 0.8,
    });

    if (!result.canceled && result.assets[0]) {
      setSelectedImage(result.assets[0].uri);
    }
  };

  const convertToBase64 = async (uri: string): Promise<string> => {
    const response = await fetch(uri);
    const blob = await response.blob();

    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64String = reader.result as string;
        resolve(base64String.split(',')[1]);
      };
      reader.onerror = reject;
      reader.readAsDataURL(blob);
    });
  };

  const handleContinue = async () => {
    if (!selectedImage) {
      Alert.alert('Photo Required', 'Please select or take a photo to continue.');
      return;
    }

    try {
      setIsLoading(true);
      const base64Image = await convertToBase64(selectedImage);
      await AsyncStorage.setItem(USER_PHOTO_KEY, base64Image);
      router.replace('/(main)/feed');
    } catch (error) {
      console.error('[ONBOARDING] Error saving photo:', error);
      Alert.alert('Error', 'Failed to save photo. Please try again.');
      setIsLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Welcome to UPLO5</Text>
        <Text style={styles.subtitle}>
          Upload a full-body photo to see yourself in amazing outfits
        </Text>
      </View>

      <View style={styles.imageContainer}>
        {selectedImage ? (
          <Image
            source={{ uri: selectedImage }}
            style={styles.preview}
            resizeMode="contain"
          />
        ) : (
          <View style={styles.placeholder}>
            <Text style={styles.placeholderText}>No photo selected</Text>
            <Text style={styles.placeholderHint}>
              For best results, use a full-body photo with good lighting
            </Text>
          </View>
        )}
      </View>

      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={styles.button}
          onPress={takePhoto}
          disabled={isLoading}
        >
          <Text style={styles.buttonText}>📷 Take Photo</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.button}
          onPress={pickImage}
          disabled={isLoading}
        >
          <Text style={styles.buttonText}>🖼️ Choose from Gallery</Text>
        </TouchableOpacity>

        {selectedImage && (
          <TouchableOpacity
            style={[styles.button, styles.continueButton]}
            onPress={handleContinue}
            disabled={isLoading}
          >
            <Text style={[styles.buttonText, styles.continueButtonText]}>
              {isLoading ? 'Loading...' : 'Continue →'}
            </Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
    padding: 20,
  },
  header: {
    marginTop: 60,
    marginBottom: 30,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#000000',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666666',
    lineHeight: 24,
  },
  imageContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    marginVertical: 20,
  },
  preview: {
    width: SCREEN_WIDTH - 80,
    height: SCREEN_HEIGHT * 0.5,
    borderRadius: 12,
  },
  placeholder: {
    width: SCREEN_WIDTH - 80,
    height: SCREEN_HEIGHT * 0.5,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#e0e0e0',
    borderStyle: 'dashed',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  placeholderText: {
    fontSize: 18,
    color: '#999999',
    marginBottom: 10,
  },
  placeholderHint: {
    fontSize: 14,
    color: '#bbbbbb',
    textAlign: 'center',
  },
  buttonContainer: {
    gap: 12,
    paddingBottom: 40,
  },
  button: {
    backgroundColor: '#f5f5f5',
    padding: 18,
    borderRadius: 12,
    alignItems: 'center',
  },
  buttonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#000000',
  },
  continueButton: {
    backgroundColor: '#000000',
    marginTop: 8,
  },
  continueButtonText: {
    color: '#ffffff',
  },
});
