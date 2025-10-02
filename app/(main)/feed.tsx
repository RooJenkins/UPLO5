import { useEffect, useRef } from 'react';
import {
  View,
  Text,
  Image,
  FlatList,
  StyleSheet,
  Dimensions,
  ActivityIndicator
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useFeed } from '../../providers/FeedProvider';
import { FeedEntry } from '../../lib/FeedLoadingService';

const { width: SCREEN_WIDTH, height: SCREEN_HEIGHT } = Dimensions.get('window');

export default function Feed() {
  const { feed, currentIndex, setCurrentIndex, workerStats, isReady } = useFeed();
  const viewabilityConfig = useRef({
    itemVisiblePercentThreshold: 50,
  }).current;

  // Preload next 5 images
  useEffect(() => {
    const nextPositions = [
      currentIndex + 1,
      currentIndex + 2,
      currentIndex + 3,
      currentIndex + 4,
      currentIndex + 5
    ];

    nextPositions.forEach(pos => {
      const item = feed[pos];
      if (item?.imageUrl) {
        Image.prefetch(item.imageUrl);
      }
    });
  }, [currentIndex, feed]);

  const renderFeedItem = ({ item }: { item: FeedEntry }) => (
    <View style={styles.feedItem}>
      {item.isLoading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#ffffff" />
          <Text style={styles.loadingText}>Generating your look...</Text>
        </View>
      ) : item.error ? (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>❌ {item.error}</Text>
        </View>
      ) : item.imageUrl ? (
        <>
          <Image
            source={{ uri: item.imageUrl }}
            style={styles.image}
            resizeMode="contain"
          />
          {item.product && (
            <View style={styles.productInfo}>
              <Text style={styles.productName}>{item.product.name}</Text>
              <Text style={styles.productBrand}>{item.product.brand_name}</Text>
              {item.product.base_price && (
                <Text style={styles.productPrice}>
                  ${(item.product.base_price / 100).toFixed(2)}
                </Text>
              )}
            </View>
          )}
        </>
      ) : null}
    </View>
  );

  const getItemLayout = (_: any, index: number) => ({
    length: SCREEN_HEIGHT,
    offset: SCREEN_HEIGHT * index,
    index,
  });

  const onViewableItemsChanged = useRef(({ viewableItems }: any) => {
    if (viewableItems.length > 0) {
      setCurrentIndex(viewableItems[0].index || 0);
    }
  }).current;

  if (!isReady) {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#ffffff" />
          <Text style={styles.loadingText}>Initializing feed...</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      {/* Worker Stats Overlay */}
      <View style={styles.statsOverlay}>
        <Text style={styles.statsText}>
          Workers: {workerStats.active}/{workerStats.max}
        </Text>
        <Text style={styles.statsText}>
          Buffer: {workerStats.bufferHealth.toFixed(0)}%
        </Text>
      </View>

      <FlatList
        data={feed}
        renderItem={renderFeedItem}
        keyExtractor={(item) => item.id}
        pagingEnabled
        showsVerticalScrollIndicator={false}
        snapToAlignment="start"
        decelerationRate="fast"
        getItemLayout={getItemLayout}
        onViewableItemsChanged={onViewableItemsChanged}
        viewabilityConfig={viewabilityConfig}
        windowSize={3}
        maxToRenderPerBatch={2}
        removeClippedSubviews={true}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  statsOverlay: {
    position: 'absolute',
    top: 60,
    right: 20,
    zIndex: 10,
    backgroundColor: 'rgba(0,0,0,0.7)',
    padding: 10,
    borderRadius: 8,
  },
  statsText: {
    color: '#ffffff',
    fontSize: 12,
    fontFamily: 'monospace',
  },
  feedItem: {
    width: SCREEN_WIDTH,
    height: SCREEN_HEIGHT,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    color: '#ffffff',
    fontSize: 16,
    marginTop: 20,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    color: '#ff6b6b',
    fontSize: 16,
  },
  image: {
    width: SCREEN_WIDTH,
    height: SCREEN_HEIGHT,
  },
  productInfo: {
    position: 'absolute',
    bottom: 80,
    left: 20,
    right: 20,
    backgroundColor: 'rgba(0,0,0,0.7)',
    padding: 16,
    borderRadius: 12,
  },
  productName: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  productBrand: {
    color: '#bbbbbb',
    fontSize: 14,
    marginBottom: 8,
  },
  productPrice: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
});
